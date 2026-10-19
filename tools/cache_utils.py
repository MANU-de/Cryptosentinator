# tools/cache_utils.py
import os
import json
import time
from functools import wraps
from pathlib import Path

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)

def disk_cache(ttl_seconds: int = 300):
    """
    Decorator that caches function return values on disk for ttl_seconds.
    If the function fails (e.g., rate-limited), it serves the stale cache as fallback.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}_" + "_".join(str(a) for a in args) + "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            safe_key = "".join(c if c.isalnum() else "_" for c in key)
            cache_file = CACHE_DIR / f"{safe_key}.json"

            now = time.time()

            # Check if cache exists and is fresh
            if cache_file.exists():
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if now - data.get("__cached_at", 0) < ttl_seconds:
                        return data.get("value")
                except Exception:
                    pass

            # Fresh fetch attempt
            try:
                result = func(*args, **kwargs)
                if result:
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump({"__cached_at": now, "value": result}, f)
                return result
            except Exception as e:
                # If network fails or rate-limited, serve stale cache if available
                if cache_file.exists():
                    print(f"[Cache Fallback] {func.__name__} failed ({e}), serving stale cache.")
                    with open(cache_file, "r", encoding="utf-8") as f:
                        return json.load(f).get("value")
                raise e

        return wrapper
    return decorator