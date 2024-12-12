import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = os.getenv("REDIS_DB", 0)

# Cache TTLs (in seconds)
CACHE_TTL_DEFAULT = 60 * 15  # 15 minutes
CACHE_TTL_USER = 60 * 60     # 1 hour
CACHE_TTL_SERVER = 60 * 5    # 5 minutes
CACHE_TTL_BALANCE = 60 * 5   # 5 minutes
CACHE_TTL_TRANSACTIONS = 60 * 30  # 30 minutes
