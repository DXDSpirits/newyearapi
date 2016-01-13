
from django.conf import settings
import redis

REDIS_CONFIG = settings.REDIS

host = REDIS_CONFIG['host']
port = REDIS_CONFIG['port']
password = REDIS_CONFIG['password']


def get_client(db=0):
    return redis.StrictRedis(host=host, port=port, password=password, db=db)
