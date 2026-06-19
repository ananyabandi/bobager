"""Caching utilities."""
from cachetools import TTLCache
from typing import Any, Optional
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class CacheManager:
    """Simple in-memory cache manager using TTLCache."""
    
    def __init__(self):
        """Initialize cache with configured TTL and max size."""
        self.cache = TTLCache(
            maxsize=settings.cache_max_size,
            ttl=settings.cache_ttl
        )
        logger.info(
            f"Cache initialized with max_size={settings.cache_max_size}, "
            f"ttl={settings.cache_ttl}s"
        )
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        value = self.cache.get(key)
        if value is not None:
            logger.debug(f"Cache hit for key: {key}")
        else:
            logger.debug(f"Cache miss for key: {key}")
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = value
        logger.debug(f"Cached value for key: {key}")
    
    def delete(self, key: str) -> None:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Deleted cache key: {key}")
    
    def clear(self) -> None:
        """Clear all cached values."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        return {
            "size": len(self.cache),
            "max_size": self.cache.maxsize,
            "ttl": self.cache.ttl,
        }


# Global cache instance
cache_manager = CacheManager()

# Made with Bob
