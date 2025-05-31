from flask_sqlalchemy import SQLAlchemy
from redis import Redis
import os

db = SQLAlchemy()
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis: Redis = Redis.from_url(redis_url, decode_responses=True)