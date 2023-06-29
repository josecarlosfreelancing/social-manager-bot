
from redislite import Redis

from app.config import Settings

redis_connection = Redis(Settings.REDIS_DB)
