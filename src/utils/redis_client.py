import os
import redis

redis_client = redis.Redis(host=os.environ.get('REDIS_SERVER_HOST', 'localhost'), port=6379)

def get_instance():
    return redis_client
