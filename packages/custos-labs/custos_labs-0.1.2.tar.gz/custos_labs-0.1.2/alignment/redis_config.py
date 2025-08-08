# alignment/redis.py

import redis_config  # GOOD

import os

r = redis_config.Redis.from_url(os.environ["REDIS_URL"])

r.set('foo', 'bar')
value = r.get('foo')