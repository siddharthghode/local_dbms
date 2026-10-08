"""
Connection pool for local_dbms.

Why pooling?
  Opening a new TCP connection + PostgreSQL auth handshake costs ~5-20 ms.
  A pool keeps N connections open and reuses them, reducing per-operation
  overhead to near zero and allowing concurrent access without exhausting
  PostgreSQL's max_connections limit.
"""
import logging

from psycopg_pool import ConnectionPool

from db.config import DB_CONFIG, POOL_MAX_SIZE, POOL_MIN_SIZE

logger = logging.getLogger(__name__)

_conninfo = (
    f"host={DB_CONFIG['host']} "
    f"port={DB_CONFIG['port']} "
    f"dbname={DB_CONFIG['dbname']} "
    f"user={DB_CONFIG['user']} "
    f"password={DB_CONFIG['password']}"
)

_pool: ConnectionPool | None = None


def get_pool() -> ConnectionPool:
    """Return the singleton connection pool, creating it on first call."""
    global _pool
    if _pool is None:
        logger.info(
            "Initialising connection pool (min=%d, max=%d) → %s:%s/%s",
            POOL_MIN_SIZE, POOL_MAX_SIZE,
            DB_CONFIG["host"], DB_CONFIG["port"], DB_CONFIG["dbname"],
        )
        _pool = ConnectionPool(
            conninfo=_conninfo,
            min_size=POOL_MIN_SIZE,
            max_size=POOL_MAX_SIZE,
            open=True,
        )
        logger.info("Connection pool ready.")
    return _pool


def close_pool() -> None:
    """Gracefully close all pooled connections on shutdown."""
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
        logger.info("Connection pool closed.")
