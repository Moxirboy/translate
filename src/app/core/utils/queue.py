from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

# Global variable for the Redis pool
pool: ArqRedis | None = None