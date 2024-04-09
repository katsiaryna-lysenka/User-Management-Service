import redis


class RedisManager:
    def __init__(self):
        self.redisClient = redis.StrictRedis(
            host="redis", port=6379, decode_responses=True
        )
        self.cache_name = "my_app_cache"


redis_manager = RedisManager()
