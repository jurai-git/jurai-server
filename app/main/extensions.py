from flask_sqlalchemy import SQLAlchemy
from redis import Redis

db = SQLAlchemy()
redis: Redis = Redis(host='localhost', port=6379, decode_responses=True)