import redis


class RedisManager:
    redisClient = redis.StrictRedis(
            host="redis", port=6379, decode_responses=True
        )

    cache_name = "my_app_cache"


redis_manager = RedisManager()


