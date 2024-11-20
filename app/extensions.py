# extensions.py
import os
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

# Setup Redis for Flask-Limiter
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.Redis.from_url(redis_url)

# Initialize Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["20 per minute"],
    storage_uri=redis_url,
    strategy="fixed-window",
)

# Initialize Flask-SQLAlchemy
db = SQLAlchemy()
