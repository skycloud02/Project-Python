import redis
import os
import json
from prometheus_client import Counter

cache_hits = Counter("cache_hits", "Number of cache hits")
cache_misses = Counter("cache_misses", "Number of cache misses")

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))

cache = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

def get_cached_result(operation: str, operand: int) -> float | None:
    key = f"{operation}:{operand}"
    try:
        value = cache.get(key)
        if value is not None:
            cache_hits.inc()
            return float(value)
        else:
            cache_misses.inc()
            return None
    except redis.exceptions.ConnectionError:
        return None

def set_cached_result(operation: str, operand: int, result: float, ttl: int = 300):
    key = f"{operation}:{operand}"
    cache.setex(key, ttl, result)
