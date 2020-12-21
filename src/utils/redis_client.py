import os
import redis

hosts = [
    "169.136.101.101",  # sg-07
    "169.136.102.52",  # sg-08
    "169.136.105.23", # sg-09
]

redis_client = redis.Redis(host=hosts[0], port=21280, password='Like_234@#$')

def get_instance():
    return redis_client


if __name__ == "__main__":
    get_instance().set('auto-deploy', 'test')
    print(get_instance().get('auto-deploy'))