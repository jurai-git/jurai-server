from flask_sqlalchemy import SQLAlchemy
from redis import Redis
import os
from dotenv import load_dotenv

<<<<<<< HEAD
db: SQLAlchemy = SQLAlchemy()
load_dotenv()
=======
db = SQLAlchemy()
>>>>>>> ada6bee4b4e871e6fc739d26a562c0498d9b1ff1
redis_url = os.getenv('REDIS_URL', 'redis://redis:6379')
redis: Redis = Redis.from_url(redis_url, decode_responses=True)