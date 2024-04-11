import redis


class RedisManager:
    redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)

    @classmethod
    def get_instance(cls):
        return cls.redis_client


redis_manager = RedisManager()



