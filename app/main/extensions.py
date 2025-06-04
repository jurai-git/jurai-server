from flask_sqlalchemy import SQLAlchemy
from redis import Redis
import os
from dotenv import load_dotenv

db: SQLAlchemy = SQLAlchemy()
load_dotenv()
redis_url = os.getenv('REDIS_URL', 'redis://redis:6379')
redis: Redis = Redis.from_url(redis_url, decode_responses=True)