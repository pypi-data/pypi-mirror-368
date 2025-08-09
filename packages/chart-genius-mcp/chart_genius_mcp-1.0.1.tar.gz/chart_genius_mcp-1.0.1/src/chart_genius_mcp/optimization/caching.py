"""
Chart Cache - Intelligent caching for performance
================================================

High-performance caching system for chart generation results.
"""

import asyncio
import time
import hashlib
import json
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ChartCache:
    """Intelligent caching system for chart generation."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """Initialize the cache."""
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.access_times = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get item from cache."""
        self.stats["total_requests"] += 1
        
        if key in self.cache:
            item = self.cache[key]
            
            # Check if expired
            if time.time() > item["expires_at"]:
                await self._remove(key)
                self.stats["misses"] += 1
                return None
            
            # Update access time
            self.access_times[key] = time.time()
            self.stats["hits"] += 1
            return item["data"]
        
        self.stats["misses"] += 1
        return None
    
    async def set(
        self,
        key: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Set item in cache."""
        
        if ttl is None:
            ttl = self.default_ttl
        
        # Evict if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            await self._evict_lru()
        
        expires_at = time.time() + ttl
        
        self.cache[key] = {
            "data": data,
            "created_at": time.time(),
            "expires_at": expires_at
        }
        
        self.access_times[key] = time.time()
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete item from cache."""
        return await self._remove(key)
    
    async def clear(self) -> bool:
        """Clear all cache items."""
        self.cache.clear()
        self.access_times.clear()
        return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        hit_rate = 0.0
        if self.stats["total_requests"] > 0:
            hit_rate = self.stats["hits"] / self.stats["total_requests"]
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": hit_rate,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "total_requests": self.stats["total_requests"]
        }
    
    async def optimize(self) -> bool:
        """Optimize cache by removing expired items."""
        current_time = time.time()
        expired_keys = []
        
        for key, item in self.cache.items():
            if current_time > item["expires_at"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            await self._remove(key)
        
        return True
    
    async def _remove(self, key: str) -> bool:
        """Remove item from cache."""
        if key in self.cache:
            del self.cache[key]
        
        if key in self.access_times:
            del self.access_times[key]
        
        return True
    
    async def _evict_lru(self) -> bool:
        """Evict least recently used item."""
        if not self.access_times:
            return False
        
        # Find LRU key
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        await self._remove(lru_key)
        self.stats["evictions"] += 1
        
        return True 


@dataclass
class RedisConfig:
    redis_url: str
    key_prefix: str = "chart_cache:"


class RedisChartCache:
    """Redis-backed intelligent caching system for chart generation."""
    def __init__(self, redis_url: str, default_ttl: int = 3600, key_prefix: str = "chart_cache:"):
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.redis_url = redis_url
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
        self._redis = None
    
    async def _client(self):
        if self._redis is None:
            try:
                import redis.asyncio as aioredis
            except Exception:
                # Fallback for older aioredis
                import aioredis as aioredis  # type: ignore
            self._redis = aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        return self._redis
    
    def _k(self, key: str) -> str:
        return f"{self.key_prefix}{key}"
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        self.stats["total_requests"] += 1
        r = await self._client()
        data = await r.get(self._k(key))
        if data is None:
            self.stats["misses"] += 1
            return None
        self.stats["hits"] += 1
        try:
            import orjson
            return orjson.loads(data)
        except Exception:
            return json.loads(data)
    
    async def set(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        r = await self._client()
        try:
            import orjson
            payload = orjson.dumps(data)
        except Exception:
            payload = json.dumps(data).encode()
        await r.set(self._k(key), payload, ex=ttl or self.default_ttl)
        return True
    
    async def delete(self, key: str) -> bool:
        r = await self._client()
        await r.delete(self._k(key))
        return True
    
    async def clear(self) -> bool:
        r = await self._client()
        # Use scan to delete keys with prefix
        cursor = 0
        while True:
            cursor, keys = await r.scan(cursor=cursor, match=f"{self.key_prefix}*")
            if keys:
                await r.delete(*keys)
            if cursor == 0:
                break
        return True
    
    async def get_stats(self) -> Dict[str, Any]:
        hit_rate = 0.0
        if self.stats["total_requests"] > 0:
            hit_rate = self.stats["hits"] / self.stats["total_requests"]
        return {
            "backend": "redis",
            "hit_rate": hit_rate,
            **self.stats
        }
    
    async def optimize(self) -> bool:
        # Redis handles expirations; nothing to do
        return True 