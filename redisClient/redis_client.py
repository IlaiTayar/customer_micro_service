from database import config
import redis


redis_client: redis.StrictRedis = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)