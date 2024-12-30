import redis
from typing import Any, Optional
import json
from datetime import timedelta

class RedisHandler:
    def __init__(self, config: dict):
        self.redis_client = redis.Redis(
            host=config['host'],
            port=config['port'],
            db=config['db'],
            password=config.get('password')
        )
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = self.redis_client.get(key)
        if value is not None:
            return json.loads(value)
        return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with optional TTL"""
        serialized_value = json.dumps(value)
        if ttl is not None:
            return self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                serialized_value
            )
        return self.redis_client.set(key, serialized_value)

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return bool(self.redis_client.delete(key))

    def flush(self) -> bool:
        """Flush all keys from cache"""
        return self.redis_client.flushdb()
