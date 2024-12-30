from typing import Any, Optional
from .redis_handler import RedisHandler

class CacheManager:
    def __init__(self, config: dict):
        self.config = config
        self.redis = RedisHandler(config['redis'])
        
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        return self.redis.get(key)

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with optional TTL"""
        return self.redis.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """Delete cached value"""
        return self.redis.delete(key)

    def clear(self) -> bool:
        """Clear all cached values"""
        return self.redis.flush()

    def get_or_set(self, key: str, value_fn: callable, ttl: int = None) -> Any:
        """Get cached value or set it if not exists"""
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value
            
        value = value_fn()
        self.set(key, value, ttl)
        return value
