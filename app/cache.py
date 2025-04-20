import json
import hashlib
import os
import redis

# Use environment variables or defaults for Redis connection details.
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Initialize the Redis client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def get_cache_key(raw_results: dict) -> str:
    """
    Generate a cache key based on the raw_results content.
    The raw_results dict is converted to a sorted JSON string and then hashed.
    """
    raw_str = json.dumps(raw_results, sort_keys=True)
    key_hash = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()
    return f"formatted_flights:{key_hash}"

def get_formatted_flights(raw_results: dict, format_function) -> dict:
    """
    Return formatted flight data using Redis as a cache.
    If the data exists in the cache, return it.
    Otherwise, call format_function(raw_results) to format the data,
    store it in Redis with a TTL (e.g., 300 seconds), and return it.
    """
    key = get_cache_key(raw_results)
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    formatted = format_function(raw_results)
    redis_client.set(key, json.dumps(formatted), ex=300)
    return formatted
