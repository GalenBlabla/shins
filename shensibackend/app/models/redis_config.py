# redis_config.py
import redis
import os
from dotenv import load_dotenv

load_dotenv()


def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
        decode_responses=True,
    )


redis_client = get_redis_client()
