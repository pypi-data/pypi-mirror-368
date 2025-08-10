"""
Base cache interface and data structures
"""
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def access(self) -> None:
        """Mark entry as accessed"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'size_bytes': self.size_bytes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary"""
        return cls(
            key=data['key'],
            value=data['value'],
            created_at=datetime.fromisoformat(data['created_at']),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            access_count=data.get('access_count', 0),
            last_accessed=datetime.fromisoformat(data['last_accessed']) if data.get('last_accessed') else None,
            size_bytes=data.get('size_bytes')
        )


class CacheInterface(ABC):
    """Abstract cache interface"""
    
    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        self.ttl = ttl
        self.max_size = max_size
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0,
            'errors': 0
        }
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries"""
        pass
    
    @abstractmethod
    async def size(self) -> int:
        """Get number of items in cache"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        pass
    
    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create deterministic key from arguments
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        
        # Serialize to JSON and hash
        key_json = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_json.encode()).hexdigest()[:32]
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.stats['hits'] + self.stats['misses']
        if total == 0:
            return 0.0
        return self.stats['hits'] / total
    
    async def get_with_stats(self, key: str) -> Optional[Any]:
        """Get value and update stats"""
        try:
            value = await self.get(key)
            if value is not None:
                self.stats['hits'] += 1
                logger.debug(f"Cache HIT for key: {key[:16]}...")
            else:
                self.stats['misses'] += 1
                logger.debug(f"Cache MISS for key: {key[:16]}...")
            return value
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache error getting key {key[:16]}...: {e}")
            return None
    
    async def set_with_stats(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value and update stats"""
        try:
            success = await self.set(key, value, ttl)
            if success:
                self.stats['sets'] += 1
                logger.debug(f"Cache SET for key: {key[:16]}...")
            return success
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache error setting key {key[:16]}...: {e}")
            return False
    
    async def delete_with_stats(self, key: str) -> bool:
        """Delete value and update stats"""
        try:
            success = await self.delete(key)
            if success:
                self.stats['deletes'] += 1
                logger.debug(f"Cache DELETE for key: {key[:16]}...")
            return success
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache error deleting key {key[:16]}...: {e}")
            return False