import os

try:
    import redis
    redis_client = redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", 6379)),
        decode_responses=True,
    )
except ImportError:
    class MockRedis:
        def get(self, key):
            return None

        def set(self, key, value, ex=None):
            pass

    redis_client = MockRedis()

